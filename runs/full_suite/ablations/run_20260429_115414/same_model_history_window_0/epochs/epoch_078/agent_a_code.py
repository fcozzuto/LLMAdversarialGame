def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    def dist(a, b):
        ax, ay = a; bx, by = b
        return max(abs(ax - bx), abs(ay - by))
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Select target resource: prefer ones where we are closer than opponent; otherwise try to minimize gap.
    if resources:
        best = None
        for i, r in enumerate(resources):
            rx, ry = r
            da = dist((sx, sy), (rx, ry))
            db = dist((ox, oy), (rx, ry))
            # Higher is better: negative gap means we are closer; add small bias to prefer nearer overall.
            score = (db - da) * 10 - da
            # Deterministic tie-break by coordinates and index
            key = (score, -rx, -ry, -i)
            if best is None or key > best[0]:
                best = (key, r)
        tx, ty = best[1]
    else:
        # No resources: head to center-ish deterministically
        tx, ty = observation.get("grid_width", 8) // 2, observation.get("grid_height", 8) // 2

    # Choose best legal move toward the target, with obstacle avoidance and mild opponent pressure.
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles:
            continue
        # Keep within bounds if engine enforces; still clamp-safe scoring.
        if 0 <= nx < observation.get("grid_width", 8) and 0 <= ny < observation.get("grid_height", 8):
            d_self = dist((nx, ny), (tx, ty))
            d_opp = dist((nx, ny), (ox, oy))
            # Prefer reducing distance to target; also slightly prefer being closer to opponent to contest.
            val = -d_self * 100 + d_opp
            # Deterministic tie-break
            candidates.append((val, -d_self, dx, dy, nx, ny))
    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True)
    return [candidates[0][2], candidates[0][3]]