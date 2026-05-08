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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    # Prefer immediate counterclaim captures; otherwise move toward opponent-controlled frontier.
    opp_targets = list(opp_terr) if opp_terr else []
    if opp_targets:
        tx, ty = min(opp_targets, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
    else:
        uc_targets = list(unclaimed)
        if uc_targets:
            tx, ty = min(uc_targets, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
        else:
            tx, ty = ox, oy

    best = None
    best_v = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        cell = (nx, ny)
        d_opp = abs(nx - ox) + abs(ny - oy)
        d_t = abs(nx - tx) + abs(ny - ty)

        if cell in opp_terr:
            v = 100 + 0.01 * d_opp - 0.02 * d_t
        elif cell in unclaimed:
            v = 30 - 0.03 * d_t + 0.005 * d_opp
        elif cell in self_terr:
            v = 10 - 0.01 * d_t + 0.002 * d_opp
        else:
            v = 2 - 0.03 * d_t + 0.001 * d_opp

        # Small deterministic bias toward continuing generally forward (away from opponent corner pressure).
        v += 0.001 * (dx * (1 if ox < sx else -1) + dy * (1 if oy < sy else -1))

        if v > best_v:
            best_v = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]