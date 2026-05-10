def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (W - 1, H - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        x, y = p[0], p[1]
        try:
            x, y = int(x), int(y)
        except Exception:
            continue
        if 0 <= x < W and 0 <= y < H:
            obstacles.add((x, y))

    self_terr = set()
    for p in observation.get("self_territory") or []:
        x, y = p[0], p[1]
        try:
            x, y = int(x), int(y)
        except Exception:
            continue
        if 0 <= x < W and 0 <= y < H:
            self_terr.add((x, y))

    opp_terr = set()
    for p in observation.get("opponent_territory") or []:
        x, y = p[0], p[1]
        try:
            x, y = int(x), int(y)
        except Exception:
            continue
        if 0 <= x < W and 0 <= y < H:
            opp_terr.add((x, y))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        x, y = p[0], p[1]
        try:
            x, y = int(x), int(y)
        except Exception:
            continue
        if 0 <= x < W and 0 <= y < H:
            unclaimed.add((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    d0 = abs(ox - sx) + abs(oy - sy)

    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H):
            continue
        if (nx, ny) in obstacles:
            continue

        gain = 0
        if (nx, ny) in opp_terr:
            gain = 8
        elif (nx, ny) in unclaimed:
            gain = 2
        elif (nx, ny) in self_terr:
            gain = 0
        else:
            gain = 1  # edge/other tiles are still controllable when entered

        d1 = abs(ox - nx) + abs(oy - ny)
        progress = d0 - d1  # prefer moving toward opponent
        score = gain * 10 + progress

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [best[0], best[1]]