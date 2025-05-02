from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from functions.load_config import load_config
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from functions.send_message import send_message


async def build_notas_detalladas(transcript):
    config = load_config()
    resume_model = None
    condensa_model = None
    # Se supone que RecursiveCharacterTextSplitter corta en parrafos o oraciones, para no romper el sentido del texto
    # a la vez que intenta mantenerse dentro de los limites establecidos
    # El chunk_size es en tokens por defecto
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config["resumeChunkSize"], chunk_overlap=0
    )
    chunks = text_splitter.split_text(transcript)

    try:
        if "claude" in config["resumeModel"]:
            resume_model = ChatAnthropic(model=config["resumeModel"], max_tokens=3072)

        if "gpt" in config["resumeModel"]:
            resume_model = ChatOpenAI(model=config["resumeModel"])

        if "claude" in config["condensaModel"]:
            # max_tokens por defecto es 1024, si intenta generar una respuesta mas grande simplemente
            # la trunca, el numero maximo depende del modelo
            condensa_model = ChatAnthropic(
                model=config["condensaModel"], max_tokens=8192
            )

        if "gpt" in config["condensaModel"]:
            # Por defecto max_tokens en ChatOpenAI is None, supongo que no tiene limite
            condensa_model = ChatOpenAI(model=config["condensaModel"])

    except Exception as e:
        print("Error al configurar los modelos, quiza falta una API_KEY")
        print(e)
        return

    # Read resume prompt from external file
    with open("resume_prompt.txt", "r", encoding="utf-8") as f:
        resume_prompt_content = f.read()

    # Build prompt template for detailed notes
    prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Eres un agente que se encarga de tomar notas detalladas sobre el texto en español. Los conceptos deben presentarse en forma detallada incluyendo una explicacion de cada idea.",
            ),
            ("user", resume_prompt_content),
        ]
    )

    # Build Resumen
    await send_message(
        {
            "action": "message",
            "msgCode": "info",
            "msg": f"Construyendo Notas ({len(chunks)} secciones)",
        }
    )
    # Crea una chain, esta la ejecutamos en un loop y no en un chain automatico
    note_chain = prompt_template | resume_model | StrOutputParser()
    notes = []
    try:
        for chunk in chunks:
            # NOTA. puede que invoke sea blocking y cause timeout del socket con la config por defecto
            # quiza se puede usar ainvoke?
            note_result = note_chain.invoke({"chunk": chunk})
            notes.append(note_result)
            await send_message(
                {
                    "action": "noteSection",
                    "note": note_result,
                }
            )
    except Exception as e:
        print(e)
        return

    notes_join = "\n\n".join(notes)

    # Read condensa prompt from external file
    with open("condensa_prompt.txt", "r", encoding="utf-8") as f:
        condensa_prompt_content = f.read()

    # Build prompt template for final document
    condensa_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Eres un agente que se encarga de entregar un Estudio Detallado sobre el texto en español. Los conceptos deben presentarse en forma detallada incluyendo una explicacion de cada idea.",
            ),
            ("user", condensa_prompt_content),
        ]
    )

    # Build Resumen
    await send_message(
        {
            "action": "message",
            "msgCode": "info",
            "msg": "Generando documento final",
        }
    )
    try:
        condensa_chain = condensa_template | condensa_model | StrOutputParser()
        final_document = condensa_chain.invoke({"notes": notes_join})
    except Exception as e:
        print(e)
        return

    if not final_document:
        print(final_document)
        return f"Error al procesar final_document, valor es null, None, falso o vacio. El largo de las notas enviadas fue {len(transcript):,}"

    return final_document