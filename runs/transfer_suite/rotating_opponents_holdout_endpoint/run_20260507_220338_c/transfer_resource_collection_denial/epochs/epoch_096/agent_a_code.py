def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Target: prefer resources we can reach earlier; break ties by closeness.
    best_t = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        key = (sd - od, sd, abs(rx - (w - 1 - sx)) + abs(ry - (h - 1 - sy)))
        if best_t is None or key < best_t[0]:
            best_t = (key, (rx, ry))
    tx, ty = best_t[1]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    res_set = set(resources)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            continue

        cur_d = man(sx, sy, tx, ty)
        nxt_d = man(nx, ny, tx, ty)
        progress = cur_d - nxt_d

        # Capturing the resource is best; otherwise prefer improving our distance and worsening opponent's.
        capture = 1.0 if (nx, ny) in res_set else 0.0
        opp_d = man(ox, oy, tx, ty)
        opp_after = man(ox, oy, nx, ny)  # proxy: moving away from our next step generally helps denial

        # Small bias to avoid getting stuck near obstacles: prefer positions not adjacent to many obstacles.
        adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if (px, py) in obst:
                    adj += 1

        score = (10.0 * capture) + (2.0 * progress) + (0.05 * (opp_d - man(nx, ny, ox, oy))) - (0.01 * adj) - (0.001 * nxt_d)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]