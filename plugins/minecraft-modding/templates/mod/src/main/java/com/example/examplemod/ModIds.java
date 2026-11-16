package com.example.examplemod;

import net.minecraft.resources.Identifier;

/** Único sitio donde se construyen identificadores "examplemod:algo". */
public final class ModIds {
    private ModIds() {
    }

    public static Identifier id(String path) {
        //? if >=1.21 {
        return Identifier.fromNamespaceAndPath(ExampleMod.MOD_ID, path);
        //?} else {
        /*return new Identifier(ExampleMod.MOD_ID, path);
        *///?}
    }
}
