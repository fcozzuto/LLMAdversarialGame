def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    sx = 0 if sx < 0 else (w - 1 if sx >= w else sx)
    sy = 0 if sy < 0 else (h - 1 if sy >= h else sy)
    ox = 0 if ox < 0 else (w - 1 if ox >= w else ox)
    oy = 0 if oy < 0 else (h - 1 if oy >= h else oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources") or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = None

    # If no visible resources, head to far corner relative to opponent.
    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: md(ox, oy, c[0], c[1]))
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    # Target resources where we have an advantage in reach (preferably winning soon).
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            nx, ny = sx, sy
        if (nx, ny) in obstacles:
            nx, ny = sx, sy

        val = -10**9
        for tx, ty in resources:
            d_me = md(nx, ny, tx, ty)
            d_op = md(ox, oy, tx, ty)
            # Advantage: pick resources we can reach earlier; add slight preference for closer ones.
            adv = (d_op - d_me)
            score = adv * 100 - d_me
            # Tie-break: if both reach in same steps, prefer resources with higher "centrality" to reduce opponent reroutes.
            if adv == 0:
                score -= md(tx, ty, (w - 1) // 2, (h - 1) // 2) * 0.1
            if score > val:
                val = score

        # Deterministic tie-break: prefer staying close to current goal line toward best estimated target.
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]