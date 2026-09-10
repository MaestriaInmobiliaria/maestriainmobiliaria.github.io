#!/usr/bin/env python3
"""Descarga las fotos de las propiedades desde el CDN publico de Prop360.

Uso:  python tools/fetch_fotos.py
Lee la tabla FOTOS de abajo y guarda cada imagen en
data/propiedades/_fotos/<slug>/01.jpg, 02.jpg ...
No necesita autenticacion (CDN publico).
"""
from __future__ import annotations
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "data" / "propiedades" / "_fotos"
CDN = "https://media.prop360.cl/publicapropiedades/img/propiedades/{}.jpg"

# slug -> lista de nombres de archivo en el CDN, en orden de publicacion
FOTOS: dict[str, list[str]] = {
    "casa-brisas-de-san-pedro": [
        "9425_Rca3axwvsNrHdt07fFgO20260906180826",
        "9425_fnwrtk0DecD9fI3zvkwb20260906180826",
        "9425_7mismxI6Wb5fPsN6qq5A20260906180826",
        "9425_qXkvNfSpQ6js0JeVfd1F20260906181915",
        "9425_PDa0UuqqeuVy5ObefVTb20260906180826",
        "9425_gLSutxnoHqI6wpcbvrrh20260906181820",
        "9425_2EcEnruBncZ91qcGrTVk20260906180826",
        "9425_LD7ygP5XZy1iDi01tlgc20260906181930",
        "9425_ekh92aWyd50odrbpeACy20260906181859",
        "9425_YaJy4WUJHnqskmfDPEjj20260906181944",
        "9425_EjuGof0vfQMcfElosvqh20260906181959",
        "9425_rh2hgXnAdkihwhx7fyST20260906182013",
        "9425_pswpxlagvO3iccCdeiKu20260906182043",
        "9425_aswcYhosGbhkerga8i5320260907131127",
    ],
    "casa-arriendo-villa-el-rosario": [
        "9289_5rttjHeofkgeEhbsvIYG20260824153557",
        "9289_rxzIdRWqkRoUPjeetglg20260807235814",
        "9289_nNe0JHgkx2V3vu85scft20260807235814",
        "9289_d7cUhZXLnqlj9DtLcqmj20260807235814",
        "9289_CercxhZC6epgtENuwVHO20260807235817",
        "9289_sj7j7xdoxDsbuYIctSnz20260807235818",
        "9289_wi5Qfb2pglrCTHkcpuwn20260807235818",
        "9289_vLoxaoRuJjpiadSNgHVb20260807235818",
        "9289_msajr6a1rb0KfpdQkI4p20260807235818",
        "9289_bA0lmoUthCgXPhjandOg20260807235818",
        "9289_eS2hcGcbsHqtng0j3cGm20260807235820",
        "9289_X9sqMT2KcllnlReHSANf20260807235823",
        "9289_i54BloyJ9prnisnwukh720260807235822",
        "9289_rquft8gjTfOfZSpbklyi20260807235823",
        "9289_zDUd9MJQG9E4XBWYa3Xw20260807235823",
        "9289_toJxyedxjqCA7lhR3gDr20260807235823",
    ],
    "casa-san-pedro-de-la-costa": [
        "9200_092kBl48TYVWGftaauLv20260727164856",
        "9200_mdOlp7aDnQoxPxadoGn620260722213020",
        "9200_khaQLj8kSSnjdTdklczm20260722211401",
        "9200_AAfydP98fVqmiTNDwlZf20260724134339",
        "9200_UbEkpfkgqcqfdcSja4is20260722211402",
        "9200_imceW8rqK6doEaT8BJbi20260722211409",
        "9200_xdj1SW9ucrPHYLufd2yp20260722211353",
        "9200_iatEkMLbybMyOfojjuuf20260724134256",
        "9200_dbTEPgdeEt0c8MerqaTm20260722211353",
        "9200_hbjakwnCXAyxwoe6gONh20260722211408",
        "9200_oNKVckIg7OFxhmUzEfuH20260722211353",
        "9200_rDHoTFckWpyNuomOwZJY20260722211353",
        "9200_pfoxtUevQFnpayhMNSds20260722211410",
        "9200_kb1tasP3huB5ekmn4Vgy20260722213641",
        "9200_gheIVQnAxFNH40sqPsb220260722211354",
    ],
    "casa-valle-san-pedro": [
        "9198_91b1d8f761f147878ff93c",
        "9198_q1NE5CUl9c8CUOuZliUd20260815030117",
        "9198_f8lHsCDZjixlXZJLsHE420260815030117",
        "9198_ukanEiwsVbYgeIgsPajx20260815030117",
        "9198_ehglc1z76bYLWaaijlxX20260815030123",
        "9198_aqoQKtbFkrJc45tcQKzK20260815030122",
        "9198_LyiKHEhua3smRLgkbjbm20260815030122",
        "9198_1kZlffkikao15j3ZwuvY20260817202217",
        "9198_jgdEidGpqBKDZvthNhBa20260815030117",
        "9198_Co72hqh6S3lxuvqUgKeo20260815030117",
        "9198_jz6g0itjfVsx9tLynv7b20260815030122",
        "9198_UquTpzgQnFur5fmwtKhl20260815030116",
        "9198_s9aHQryzpyKnwqU976ay20260815030122",
        "9198_yQ0RhtmcfcwgaOa4hlrd20260817202156",
        "9198_ydIpxkE8FZncqPlrBpJ820260817202206",
        "9198_dk29DJo9spde4eBEmn7V20260817202213",
        "9198_3bIGbRlWyrraab70qfec20260817202659",
    ],
    "departamento-aires-de-chiguayante": [
        "9157_f4505cc1fdf54f4182349a",
        "9157_b1cb569166004eaa843267",
        "9157_58ae357b306d44779ad821",
        "9157_cadacd935e4442dca10eb3",
        "9157_6d01fc5ea50d437990eeff",
        "9157_00d95f4fa912424ea731c8",
        "9157_067c759da3c24ed090894a",
        "9157_ac6a382049734686abaabb",
        "9157_d7351919c3da4a9baa33be",
        "9157_94043ae0b251481ca21cc8",
        "9157_ea81133d8f9e46dca5637e",
        "9157_6fe8e3d420bb4df185bb83",
        "9157_e493facff0d94185b4f1f9",
        "9157_5096acfc97af45e28f1e4d",
        "9157_45ddc0503e1748228ad962",
        "9157_0a46b16d52024cc39be472",
        "9157_65b8c3b7bd6a4e62a642da",
        "9157_b1ab9a3714af46218ac6e4",
        "9157_bc42ac692b8c42c2a7f708",
        "9157_1317a1ce9f154347ac3fa8",
    ],
    "departamento-janequeo-concepcion": [
        "9154_49c3ae1131ec4856af5b52",
        "9154_fe136a3cc37e4946880764",
        "9154_0181fa0a3a2e4327ba2448",
        "9154_0c74f058a58b435caad517",
        "9154_807bf213226b462989ae72",
        "9154_cd76914cd61d495ba4c002",
        "9154_f3a3a8b2ee89496993905b",
        "9154_f1ead062b90e411d83ec64",
        "9154_abe77c2fe6cd46888ad266",
        "9154_e2e980df751b4c72823717",
        "9154_836cbe6c686b4ab2990809",
        "9154_b61a40ee8b2d48218d2a40",
    ],
    "casa-calle-uno-concepcion": [
        "9081_931ef070db07489782bea9",
        "9081_17cdd9d333154d4a920ae9",
        "9081_f0a277bb67864f7f856498",
        "9081_acce130475ca4c9fb382a7",
        "9081_484269ebbda54660bcf5de",
        "9081_7f8f3bdea0a84e6b8f1678",
        "9081_2c8d9f35af9d4e4b993cb5",
        "9081_a7e5171b68cc46f28f18b8",
        "9081_f5bdd8153ff946fd822dfe",
        "9081_44d8a03de848498f89cffe",
        "9081_2aa6a9f492b74615bf3602",
        "9081_71212caeb79344fdb75da4",
    ],
    "departamento-edmundo-larenas": [
        "9074_a3f2f0113dd2439c807be3",
        "9074_e50b6cf772124295a07c92",
        "9074_52c642c9be0044fb90f272",
        "9074_2606566f327044ff827a8a",
        "9074_1b14f6b26c4e429bbd8874",
        "9074_1d2e9cd106e5494d911839",
        "9074_4a12ab545a30458c882785",
        "9074_37aa54ca94b9439686b903",
        "9074_0ddae9f23a954c9e93d6ea",
        "9074_ef8a7f346c5649d7bd9a7a",
    ],
    "casa-villa-el-rosario-lomas-coloradas": [
        "9009_a243934b5db3412b9f914e",
        "9009_4c8842b26a1846d3a89a0f",
        "9009_159d97a96051457a89edba",
        "9009_97c1ea39e5b147fca07a42",
        "9009_c62198affb5147f7b4fe99",
        "9009_ef2c8262bff64928993eb8",
        "9009_e1405a0d8de5453b9512de",
        "9009_cb313c3c925e4927a407d1",
        "9009_21770e351f5640369ac634",
        "9009_db04ecc647714bb5a8a422",
        "9009_46dbf6f9c6554475aeae80",
        "9009_a28ca1d372224f73972f66",
        "9009_074b763c7b3a4f818a1304",
        "9009_29789e243bd74479b1d00e",
        "9009_4e179973be0747b88a1d85",
        "9009_4785e3bd633240749bc5a6",
        "9009_9c0f77b4fa18411b94580d",
        "9009_450f5d6b37f449e4b823e2",
        "9009_a0e204b758ba4e808b9f9a",
        "9009_8ea36c4f423b4981aa9a88",
        "9009_8e2fc7b86ed54c339b842f",
    ],
    "departamento-vivo-huerto-huertos-familiares": [
        "9008_fed9eb142f1c4a1cbd36f8",
        "9008_69749ec945ab4764a3bad1",
        "9008_2b0f33e85204470b87e1b1",
        "9008_363fc472679a433993c518",
        "9008_e5a4a9b18c2f4f5fa0407a",
        "9008_a1f0a5e3a23f48269f1d6f",
        "9008_d6028568ca84459bae0365",
        "9008_48e1c5cfab4f4bd2aebb02",
        "9008_6e9c3493f1ba4baaab4d81",
        "9008_bda9c7adc1ed4defb5471b",
        "9008_1dad3d75a42b49038ef414",
        "9008_af42e2c44a3a488d8f6102",
        "9008_b770e6da764240dea86452",
        "9008_e6e82645393b478a94d892",
        "9008_8ffa37ad68dd4a6a91acf8",
        "9008_59b378b36b03473588d8e9",
        "9008_8ba9545cc9024f09b00277",
    ],
    "departamento-parque-lomas-san-sebastian": [
        "9004_181853e642e541d7887932",
        "9004_c20f63d03a3346a7a727c8",
        "9004_48f169fd62e644b982a683",
        "9004_07a0919cedbf402a807736",
        "9004_4406ed7640cd4044ab458b",
        "9004_9cdc821c56fc4c4fb65e17",
        "9004_52fe9331c7d94cd0a74a80",
        "9004_3678cd779e454157b1eb7d",
        "9004_6fea5027cb304d4caa0511",
        "9004_0c83cb7122934c39906d01",
        "9004_66cafb9d973046678afa91",
        "9004_a7ee40bf91c6408eb6a867",
        "9004_4be56733780f45ea8a0cb0",
        "9004_90230ab33b7747f28a298e",
        "9004_fbb1e05c30b84643b6e091",
        "9004_cce0778aa19b4ec1b8ba16",
        "9004_891267bdedf14f23a3da08",
        "9004_92fb1366c50c450ca9c27d",
        "9004_de11c6fa14ca49598b9de4",
    ],
}

HDRS = {"User-Agent": "Mozilla/5.0", "Referer": "https://publicapropiedades.prop360.cl/"}


def main() -> int:
    total = ok = 0
    for slug, nombres in FOTOS.items():
        carpeta = DEST / slug
        carpeta.mkdir(parents=True, exist_ok=True)
        for i, nombre in enumerate(nombres, 1):
            total += 1
            out = carpeta / f"{i:02d}.jpg"
            if out.exists() and out.stat().st_size > 2000:
                ok += 1
                continue
            url = CDN.format(nombre)
            try:
                req = urllib.request.Request(url, headers=HDRS)
                data = urllib.request.urlopen(req, timeout=30).read()
                if len(data) < 2000:
                    print(f"  ! {slug}/{i:02d}  respuesta muy chica ({len(data)} b)")
                    continue
                out.write_bytes(data)
                ok += 1
                print(f"  OK {slug}/{i:02d}.jpg  ({len(data)//1024} KB)")
            except Exception as e:  # noqa: BLE001
                print(f"  ! {slug}/{i:02d}  {e}")
    print(f"\n{ok}/{total} fotos descargadas")
    return 0 if ok == total else 1


if __name__ == "__main__":
    sys.exit(main())
