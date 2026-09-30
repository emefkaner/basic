# Ablage für IRON-CLOUD-Generierungen (Higgsfield)

Jede Bild- oder Videogenerierung für IRON CLOUD wird direkt im Higgsfield-Projekt
„IRON CLOUD" einsortiert. **Nie ohne Zielordner generieren.**

```
Workspace-ID  db9c3bdd-1fc9-4b35-8e50-9ee3572cebaf
Projekt-ID    1d392fa4-c334-4367-b7a3-8e2ccddf22f8
```

## Ordner in der Projektwurzel

| Ordner | ID | Inhalt |
|---|---|---|
| `_SHOTLIST` | `d38253d0-51eb-4e47-98f1-0fb8a4376f70` | alle Shots, Unterordner pro Szene |
| `LOCATION` | `f6e88a4e-9b14-4b70-9b7a-e9ae24d4c4ae` | Location-Platten und Umgebungen |
| `CHARACTER` | `7ff3e40d-ff8a-4b20-ba5d-97adfc72fb6d` | Figuren-Referenzen |
| `INTRO` | `60785877-bd9c-4652-a5ee-f1b4bd251e5f` | Intro |
| `TESTSHOTs` | `167cef42-4653-4abe-858e-bc342ed70419` | Tests ohne Shotnummer |
| `_` | `7e3fa50b-86ea-48bd-a64e-e84a91dfaefe` | stand nicht in der Übergabe — Zweck unklar, nichts hineinlegen |

## Szenenordner unter `_SHOTLIST`

Abgefragt am 2026-09-30 per `list_folders`. Die Liste driftet; vor dem Einsortieren
neu abfragen, statt eine ID von hier zu vertrauen.

| Szene | Folder-ID |
|---|---|
| S01 | `9db0f59b-2d11-410c-8f61-7f36fb9a3006` |
| S02 | `3804e11d-cdc6-4d10-9b0a-e4dec3d18b08` |
| **S03** | `528885e4-cf89-47e6-902f-0213b35d5303` |
| S04 | `69663daa-0510-4e62-a41f-66b32206b22e` |
| S05 | `19c8db0e-5d85-4c54-a9a7-ea0c9295ae6e` |
| S05 INFLATE | `2832eb43-aad1-4d74-9525-25b31317652c` |
| S06 | `b3225400-382f-4cd9-bb5a-5d03b16c9cbe` |
| S07 | `46697a3b-18cb-44d5-8a1b-8304b393dd16` |
| S08 | `0a5528c5-30c2-4ff7-99a0-17c802111585` |
| S09 | `81fd8674-2651-453c-9930-d15a314d502d` |
| S10 | `24effd21-1e18-4ba8-b5ee-1e75d411281a` |
| S11 | `9fbe72b5-7583-42e7-97d3-5201d691919b` |
| S13 | `f531b421-4089-4c60-aa36-844c93735273` |
| S14 PROPS OUT | `779c37ce-df8c-4097-8591-74ed13ba07ec` |
| S15 LIFTOFF | `f2abdd5c-0ce2-4cc2-8636-f5cc2ce5d012` |
| S16 | `f398dad7-094a-46a7-953d-670576bacd03` |
| S17 | `f6d11f64-147b-4f42-add4-eb611d354f69` |
| S18 | `00e16d68-d79d-47a1-b888-825fd1d836ba` |
| S19 | `6767187b-f604-4ecb-8ab7-1d330b70e953` |
| S20 | `fd1136f9-2214-4e7a-bbb5-2620f13005b9` |
| S23 | `f673bab8-b272-402c-a3ea-31ad70d93c7a` |
| S24 | `f42119c9-b8b8-49b3-956e-547925819f22` |
| S25 | `288e3c27-0447-4ba6-848d-4bf54fb3b622` |
| H264 | `666a7fb2-20bf-486a-94c1-edf58107e2f2` |
| `_` | `d3b7f085-2929-4c68-bed6-686a29ef77c6` |

**S12, S21 und S22 haben keinen Ordner.** Fällt einer davon an, erst fragen, ob er
angelegt werden soll — nicht stillschweigend `create_folder` aufrufen.

## Regeln

1. Eine Shotnummer `19_01` heißt Szene 19 und gehört nach `_SHOTLIST/S19`. Bestätigt:
   `S19` existiert und die Nummerierung deckt sich mit den vorhandenen Ordnern.
2. *(offen — die Übergabe brach nach Regel 1 ab; Regeln 2 ff. fehlen und sind beim
   User nachzufragen, bevor irgendetwas einsortiert wird.)*

## Wie man einsortiert

`list_folders` und `list_project_assets` sind kostenlos und brauchen beide
`workspace_id` **und** `project_id`. Für die Unterordner einer Szene
`parent_folder_id` mitgeben. Vor dem Generieren den Zielordner nachschlagen, nicht aus
dieser Datei raten.

Reine Referenz-Elemente (`show_reference_elements`) liegen **nicht** in dieser Struktur
— sie haben gar kein Ordnerfeld und werden über Namenspräfix und Beschreibung sortiert.
Die Ordner hier gelten für Generierungen und Uploads.
