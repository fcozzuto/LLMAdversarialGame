def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx + dy  # Manhattan works well with diagonal-allowed moves

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    # Choose move that maximizes competitive margin to some resource (prefer taking ahead of opponent)
    best_move = None
    best_score = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        my_pos = (nx, ny)
        # Evaluate a limited subset deterministically to keep it small
        # Sort resources by immediate proximity to reduce work deterministically
        res_sorted = sorted(resources, key=lambda t: dist(my_pos, t))
        score = -10**18
        for i in range(min(6, len(res_sorted))):
            t = res_sorted[i]
            myd = dist(my_pos, t)
            opd = dist((ox, oy), t)
            margin = opd - myd  # positive means we are closer or can reach sooner
            # Tie-break: prefer smaller myd slightly and avoid paths that are too slow
            cand = margin * 1000 - myd
            # If we can "arrive" at same turn with diagonal moves, boost (using parity-ish tie)
            if myd <= 1:
                cand += 500
            # Also lightly discourage moving away from center line toward remaining resources
            score = max(score, cand)
        # Small preference for moves that also reduce distance to the closest resource overall
        closest_now = dist((sx, sy), res_sorted[0])
        closest_next = dist((nx, ny), res_sorted[0])
        total = score - (closest_next - closest_now) * 2
        if total > best_score:
            best_score = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]