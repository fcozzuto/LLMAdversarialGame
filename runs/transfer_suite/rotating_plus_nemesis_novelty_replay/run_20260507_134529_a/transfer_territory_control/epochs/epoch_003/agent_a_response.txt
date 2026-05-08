def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set_pos(key):
        pts = observation.get(key, []) or []
        out = set()
        for p in pts:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                out.add((int(p[0]), int(p[1])))
        return out

    obstacles = to_set_pos("obstacles")
    unclaimed = to_set_pos("unclaimed_cells")
    self_terr = to_set_pos("self_territory")
    opp_terr = to_set_pos("opponent_territory")

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    # Choose a chase target: prefer nearby opponent-territory (counter-claim); else unclaimed.
    if opp_terr:
        targets = list(opp_terr)
    elif unclaimed:
        targets = list(unclaimed)
    else:
        targets = [(ox, oy)]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = (0, 0)
    bestv = -10**18
    # Fixed tie-break by move order; slight deterministic bias based on turn parity.
    parity = int(observation.get("turn_index", 0)) & 1

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        v = 0
        if (nx, ny) in unclaimed:
            v += 140
        if (nx, ny) in opp_terr:
            v += 110
        if (nx, ny) in self_terr:
            v += 18

        tdist = min(dist((nx, ny), t) for t in targets) if targets else 0
        v -= 3 * tdist

        # Push toward opponent side; stay aggressive in general.
        v -= 0.5 * dist((nx, ny), (ox, oy))

        # Mild preference to avoid idling unless beneficial.
        if dx == 0 and dy == 0:
            v -= 8

        # Deterministic micro-bias to reduce symmetric oscillations.
        v += (0.01 if ((nx + ny + parity) % 2 == 0) else -0.01)

        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]