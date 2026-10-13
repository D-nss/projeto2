CRIPTOGRAMAS = {
    "F01": [
        (0xf918fb59ce, "2312"),
        (0x1ff205f612, "3f82d9592c02"),
        (0x1569db9f79, "23ad2dd622003772f51825ad2dd6280037"),
        (0x3a6ef7760a, "37b12f5add3236131de367a03259c23236540be421aa2110827e60"),
        (0x0538bcb4fe,
            "f9c833156814ea128c93dbde2a54321ce25c9290d5c867102f59fa11df90d0"
            "d4241b601caf089a8ec8da671b6c14e01890d2ffef15"),
    ],
    "S01": [
        (0x2a6ca6dae1, "f20b4ee2a94adef11faba11de987fc1f9a5a0d94e047dabda34cdb5254"),
        (0xd4deea0cad,
            "d3a2040ff515c047c78c2abdabc1f502956682d639abaa1af91c456f5eb92e"
            "bd"),
        (0x46fc2a2db6, "cda942d108a51df75a00a4a616d515f215405491f6ab59ca06"),
        (0x6102fc2bed,
            "3ea85f11ec220e1948ef69b2e948a9350c1413cb6aa1f9946d7bd91754a67b"
            "a7e804683e9f034dde26a35391ba38191e0dca25ee51dd6134d106479f39bb59"
            "926230d05259ca7db5accc293e4f1a2bae7aa2"),
        (0xa912c6afad, "d1914510507140490bf685"),
    ],
    "S02": [
        (0x753e5713d4,
            "8dd53187c5733c9d730dac943dc8cd7268967c06e3d231ce807e3a917ca5a2"
            "943fcece7929d87ce1b3dd24ddc13d398d7409aad73f87d1682dd86f0caedb28"
            "c2807e29947caeb1d12dc6806d298a7ce1b0d12c87cd7c218b3da7a2d737cb80"
            "792d9e7407aac67ed2cd7c68976d0cb1d53dc6cf3d38996fa0e3c13387c3723a"
            "8872eca5dd30ced472689c7849b3dd24ddc16e"),
        (0x3ec9997508,
            "da042e02f87c689c7243c8452103f57e209d3d19f4402a05fd7c68997ea0f9"
            "453d57e170688872b4f84b6f1af5743bd86f02eb4d2b18b46d298a7c49fe4a3b"
            "05f56f68967ce1e8452316b4792dd870a2a31c7657f8722f9733"),
        (0x8b9acff206,
            "53433305ed69299578076f497d01fd752d913d0e6e45290fbe74268c78b97e"
            "5f2e01f0692dd87ceb72483809ff3d2c973d1d7e5f2905be792dd86e067c592f"
            "01f07e29d85e9b5a"),
        (0x564c542a37,
            "aa47be1b3eac3d9d3d068604a31a6dfd2a977310cb17e65473b4268d69a498"
            "04a51173fd269d73a39e49f61771b3209d7e058641b80071fd2e976f02cb4bf6"
            "127fa927d879a1cb55a3113eb2688c78b39f4bf6116da929d87ea28d56b71071"
            "f1688d7002cb54b3076db229d86c168a48a7017baf689c7ceb8e54b9177ffd39"
            "8d78e49845b41d7ffd249d6f438e04b3077daf2d8e781ecb47b91a6db82f8d74"
            "aacb55a3117caf298a3d02cb47bf126cbc689c78438841a5156c"),
        (0x8e321416e4,
            "d0e80284fb3d0c97680bf3e60ee0d14e68967c0cbfe74bd1b47f279531ebf1"
            "e64384fb3d7bbc5898b3a343c5e73d268d730afea35ac1fa69298a7c0ebfec0e"
            "90d0581bd43dbaeae64384e77c2a9d22"),
    ],
}


def mensagens(identificador):
    return [(iv, bytes.fromhex(texto)) for iv, texto in CRIPTOGRAMAS[identificador]]
