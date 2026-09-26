import request from './request'

export const getCities = () => request.get('/base/cities')
export const searchFlights = (params) => request.get('/flights', { params, silent: true })
export const getFlightDetail = (flightNo) => request.get(`/flights/${flightNo}`)
