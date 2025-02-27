declare global {
    namespace NodeJS {
        interface ProcessEnv {
            GISCUS_REPO_ID: string;
            GISCUS_CATEGORY_ID: string;
        }
    }
}