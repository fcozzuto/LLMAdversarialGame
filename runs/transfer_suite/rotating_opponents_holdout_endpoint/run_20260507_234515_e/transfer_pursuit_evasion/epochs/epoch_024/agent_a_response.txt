def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    srole = str(observation.get("self_role", "")).lower()
    is_pursuer = any(k in srole for k in ("purs", "catch", "seeker", "chase"))
    is_evader = any(k in srole for k in ("evad", "runner", "escape", "flee"))

    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((int(p[0]), int(p[1])))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in oset:
            continue

        d = max(abs(nx - ox), abs(ny - oy))  # Chebyshev works with diagonal moves
        # obstacle-adjacent penalty
        adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in oset:
                    adj += 1

        if is_evader or not is_pursuer:
            # flee: maximize distance; prefer corners opposite pursuer; avoid obstacle adjacency
            corner_dist = max(max(abs(cx - ox), abs(cy - oy)) for (cx, cy) in corners)
            # choose better corner relative to our position deterministically
            our_corner = min(corners, key=lambda c: abs(c[0] - nx) + abs(c[1] - ny))
            corner_bonus = (abs(ox - our_corner[0]) + abs(oy - our_corner[1])) // 1
            score = (d, corner_bonus, -adj, -abs(nx - sx) - abs(ny - sy))
            if best_score is None or score > best_score:
                best_score = score
                best_move = [int(dx), int(dy)]
        else:
            # pursue: minimize distance; reduce relative axis difference; avoid obstacle adjacency
            axis = abs(nx - ox) + abs(ny - oy)
            score = (-d, -axis, -adj, -abs(nx - sx) - abs(ny - sy))
            if best_score is None or score > best_score:
                best_score = score
                best_move = [int(dx), int(dy)]

    return [int(best_move[0]), int(best_move[1])]