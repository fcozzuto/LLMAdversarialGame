def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    opp_list = list(opp_t) if opp_t else [(ox, oy)]
    dirs = [(0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def adj_to_set(x, y, S):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in S:
                    return True
        return False

    best = (float("-inf"), 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue

        v = 0.0
        if (nx, ny) in opp_t:
            v += 50.0
        elif (nx, ny) in self_t:
            v += 6.0
        elif (nx, ny) in unclaimed:
            v += 18.0
            if opp_t and adj_to_set(nx, ny, opp_t):
                v += 14.0

        if opp_list:
            md = 10**9
            for px, py in opp_list:
                d = abs(nx - px) + abs(ny - py)
                if d < md:
                    md = d
            v -= md * 0.25

        if v > best[0]:
            best = (v, dx, dy)
        elif v == best[0]:
            if (dx, dy) < (best[1], best[2]):
                best = (v, dx, dy)

    return [int(best[1]), int(best[2])]