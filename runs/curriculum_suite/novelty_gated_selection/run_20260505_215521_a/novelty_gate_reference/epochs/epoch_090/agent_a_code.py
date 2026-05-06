def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best_move = (0, 0)
    best_score = -10**18

    # Prefer: move toward a resource where opponent is farther, and avoid giving opponent the edge.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # Choose target resource deterministically: maximize denial gap and our progress after move.
        target_score = -10**18
        for tx, ty in resources:
            sd = man(nx, ny, tx, ty)
            od = man(ox, oy, tx, ty)

            # Encourage immediate pickup/near pickup.
            pickup = 7 if sd == 0 else 0
            # If opponent can get there sooner, penalize strongly.
            denial = (od - sd)
            # If we are very far from any resource, steer toward nearest.
            progress = -sd

            # Edge_patrol-ish bias: slightly prefer moving along our side toward the map center when tied.
            edge_bias = 0
            if nx in (0, w - 1) or ny in (0, h - 1):
                edge_bias = -0.25 * (abs(nx - (w // 2)) + abs(ny - (h // 2)))

            cand = pickup + 2.2 * denial + 0.7 * progress + edge_bias
            if cand > target_score:
                target_score = cand

        # Also include a small term to keep us away from obstacles by not stepping adjacent to many obstacles.
        adj_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if (nx + ax, ny + ay) in obstacles:
                    adj_pen += 0.15
        total = target_score - adj_pen

        # Deterministic tie-break: smallest dx, then smallest dy.
        if total > best_score or (total == best_score and (dx, dy) < best_move):
            best_score = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]