def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    opp_terr = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            opp_terr.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles and (x, y) not in opp_terr

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    bestv = None

    if unclaimed:
        # Pick move that minimizes distance to nearest unclaimed; tie-break deterministically.
        for dx, dy in moves:
            x, y = sx + dx, sy + dy
            if not valid(x, y):
                continue
            md = None
            for ux, uy in unclaimed:
                d = abs(ux - x) + abs(uy - y)
                if md is None or d < md:
                    md = d
            v = -md if md is not None else -10**9
            if best is None or v > bestv:
                best, bestv = [dx, dy], v
    else:
        # No unclaimed data: move to maximize distance from opponent.
        for dx, dy in moves:
            x, y = sx + dx, sy + dy
            if not valid(x, y):
                continue
            d = abs(ox - x) + abs(oy - y)
            v = d
            if best is None or v > bestv:
                best, bestv = [dx, dy], v

    if best is None:
        # Fallback: any in-bounds non-obstacle move; prefer stay last.
        for dx, dy in moves[:-1] + [(0, 0)]:
            x, y = sx + dx, sy + dy
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles and (x, y) not in opp_terr:
                return [dx, dy]
        return [0, 0]
    return best