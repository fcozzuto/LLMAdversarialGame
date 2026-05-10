def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    cx, cy = w // 2, h // 2
    opp_pos = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_sc = -10**18

    # Small deterministic bias to keep moving toward opponent/capture fronts.
    move_phase = int(observation.get("turn_index", 0) or 0) % 2
    bias_to = (cx, cy) if move_phase == 0 else (ox, oy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        sc = 0
        if (nx, ny) in self_terr:
            sc += 0.5
        elif (nx, ny) in opp_terr:
            sc += 4.0  # capture by flipping
        elif (nx, ny) in unclaimed:
            sc += 3.0  # expand territory

        # Prefer getting closer to center and also near opponent for counterclaiming.
        sc += 1.2 * (-(abs(nx - cx) + abs(ny - cy)))
        sc += 0.6 * (-(abs(nx - ox) + abs(ny - oy)))

        # Avoid wasting moves by not heading farther from our bias target.
        sc += 0.4 * (-(abs(nx - bias_to[0]) + abs(ny - bias_to[1])))

        # Slight preference to progress (avoid staying still unless necessary).
        if dx == 0 and dy == 0:
            sc -= 0.2

        # Deterministic tie-break: fixed dir iteration order already provides this if sc equal.
        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    return best if best is not None else [0, 0]