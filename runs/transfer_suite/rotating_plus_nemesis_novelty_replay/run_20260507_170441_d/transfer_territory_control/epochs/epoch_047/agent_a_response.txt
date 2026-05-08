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

    cx, cy = w // 2, h // 2
    tmix_x = (sx + ox) // 2
    tmix_y = (sy + oy) // 2
    # Bias target toward center while staying between agents (interference plan)
    tx = max(0, min(w - 1, (tmix_x + cx) // 2))
    ty = max(0, min(h - 1, (tmix_y + cy) // 2))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = [0, 0]
    bestv = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            nx, ny, dx, dy = sx, sy, 0, 0

        v = 0
        if (nx, ny) in opp_t:
            v += 1800  # prefer stealing
        elif (nx, ny) in self_t:
            v -= 40    # avoid just orbiting our own claim
        elif (nx, ny) in unclaimed:
            v += 220   # claim new cells
        else:
            v += 10

        # Interfere: reduce distance to interference target and opponent
        d_t = abs(nx - tx) + abs(ny - ty)
        d_o = abs(nx - ox) + abs(ny - oy)
        v += 140 - 25 * d_t
        v += 90 - 18 * d_o

        # Also slightly gravitate toward center (opponent is center-claimer)
        v += 10 - 6 * (abs(nx - cx) + abs(ny - cy))

        if v > bestv or (v == bestv and (dx, dy) < (best[0], best[1])):
            bestv = v
            best = [dx, dy]

    return [int(best[0]), int(best[1])]