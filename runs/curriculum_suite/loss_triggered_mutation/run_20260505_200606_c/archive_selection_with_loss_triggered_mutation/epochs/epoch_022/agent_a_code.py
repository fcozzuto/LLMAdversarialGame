def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    res = resources
    best = None
    best_sc = -10**18

    def closest_res_dist(x, y):
        md = 10**9
        for r in res:
            rx, ry = r
            d = abs(rx - x) + abs(ry - y)
            if d < md:
                md = d
        return md if res else md

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or not ok(nx, ny):
            continue
        d_to_res = closest_res_dist(nx, ny)
        d_to_opp = abs(ox - nx) + abs(oy - ny)
        score = 1000 - d_to_res - 2 * d_to_opp
        if score > best_sc:
            best_sc = score
            best = [dx, dy]

    if best is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and ok(nx, ny):
                return [dx, dy]
        return [0, 0]
    return best