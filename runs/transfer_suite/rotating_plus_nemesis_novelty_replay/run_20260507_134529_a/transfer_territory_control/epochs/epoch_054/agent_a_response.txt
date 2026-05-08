def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        out = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.add((x, y))
        return out

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    candidates = []
    opp_list = list(opp_terr)[:64]  # cap for speed/determinism

    def mdist_to_opp(x, y):
        if opp_list:
            m = 10**9
            for tx, ty in opp_list:
                d = abs(x - tx) + abs(y - ty)
                if d < m: m = d
            return m
        return abs(x - ox) + abs(y - oy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        safety = mdist_to_opp(nx, ny)
        closer_to_opp = -(abs(nx - ox) + abs(ny - oy))
        gain = 0.0
        if (nx, ny) in unclaimed:
            gain += 2.0
        elif (nx, ny) in opp_terr:
            gain += 1.5
        elif (nx, ny) in self_terr:
            gain += 0.2
        # Prefer filling nearby territory while keeping distance from opponent's current edge
        score = gain + 0.9 * safety + 0.15 * closer_to_opp
        candidates.append((score, dx, dy, nx, ny))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (t[0], -t[3], -t[4], t[1], t[2]))
    _, dx, dy, _, _ = candidates[-1]
    return [int(dx), int(dy)]