def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            if "pos" in r and r["pos"] is not None and len(r["pos"]) >= 2:
                resources.append((int(r["pos"][0]), int(r["pos"][1])))
            elif "x" in r and "y" in r and r["x"] is not None and r["y"] is not None:
                resources.append((int(r["x"]), int(r["y"])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(a, b, c, d):
        ax = a - c
        if ax < 0: ax = -ax
        ay = b - d
        if ay < 0: ay = -ay
        return ax if ax >= ay else ay

    if not resources or not inb(sx, sy):
        return [0, 0]

    # Pick a target resource that we can reach relatively earlier than the opponent
    best_res = None
    best_val = -10**9
    best_self_dist = 10**9
    for rx, ry in resources:
        if not inb(rx, ry):
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources where opponent is relatively far; break ties toward closer-for-us
        val = (od - sd) * 10 - sd
        if val > best_val or (val == best_val and sd < best_self_dist):
            best_val = val
            best_self_dist = sd
            best_res = (rx, ry)

    if best_res is None:
        return [0, 0]
    tx, ty = best_res

    # Choose best next step among valid moves (greedy toward target, but also avoid getting too close to opponent)
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    deltas.sort()
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        new_sd = cheb(nx, ny, tx, ty)
        new_od = cheb(nx, ny, ox, oy)
        # Primary: minimize distance to target; Secondary: keep opponent farther
        score = -new_sd * 100 - cheb(nx, ny, ox, oy)
        # Deterministic tie-break: prefer lexicographically smaller move
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]