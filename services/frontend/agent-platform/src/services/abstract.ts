import { AxiosRequestConfig } from "axios";


export const getAxiosEmptyConfig = (): AxiosRequestConfig => { 
    const axiosConfig = {
        headers: {},
        params: {},
        validateStatus: () => true
    }
    return axiosConfig
}

export const getAxiosAuthConfig = (accessToken: string): AxiosRequestConfig => {
    const axiosConfig = getAxiosEmptyConfig();

    axiosConfig["headers"] = {
        "Authorization": `Bearer ${accessToken}`
    }

    return axiosConfig;
}

abstract class RESTService {
    protected readonly baseUrl: string = "http://127.0.0.1:8000"; // TODO: TO ENV!
    protected readonly baseRoute: string;

    constructor(baseRoute: string) {
        this.baseRoute = baseRoute
    }

    protected url(route: string = "", id: string | null = null): string {
        const url = `${this.baseUrl}${this.baseRoute}${route}`;

        if (id == null) {
            return url
        }

        return `${url}/${id}`
    }
}

export default RESTService;
