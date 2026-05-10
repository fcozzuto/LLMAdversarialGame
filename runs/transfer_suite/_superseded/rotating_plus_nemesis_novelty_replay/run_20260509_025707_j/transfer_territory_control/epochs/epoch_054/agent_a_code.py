def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    my = set((p[0], p[1]) for p in (observation.get("self_territory") or []))
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory") or []))
    un = set((p[0], p[1]) for p in (observation.get("unclaimed_cells") or []))
    obs = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    ox, oy = observation["opponent_position"]
    myc = observation.get("self_territory_count", len(my))
    opc = observation.get("opponent_territory_count", len(opp))
    behind = myc < opc

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def adj_opp(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in opp:
                    return True
        return False

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-1e9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        gain = 0.0
        if (nx, ny) in opp:
            gain += 2.0
        elif (nx, ny) in un:
            gain += 1.0
        elif (nx, ny) in my:
            gain += 0.0
        else:
            gain += 0.0

        d_opp = manh(nx, ny, ox, oy)
        if behind:
            gain += (0.6 if (nx, ny) in un and adj_opp(nx, ny) else 0.0)
            gain += (0.25 if (nx, ny) in opp else 0.0)
            gain -= 0.03 * d_opp
        else:
            gain += (0.12 if (nx, ny) in un and not adj_opp(nx, ny) else 0.0)
            gain += 0.02 * d_opp

        if gain > best[0]:
            best = (gain, dx, dy)

    return [best[1], best[2]]