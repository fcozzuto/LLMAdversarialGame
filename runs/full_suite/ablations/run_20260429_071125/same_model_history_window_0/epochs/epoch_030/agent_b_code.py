def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def best_move(target):
        tx, ty = target
        best = [0, 0]
        best_score = -10**9
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if nx < 0 or nx >= w or ny < 0 or ny >= h:
                    continue
                if (nx, ny) in obstacles:
                    continue
                # Prefer getting closer to target; avoid opponent; slightly bias toward staying away from obstacles indirectly.
                dist_t = abs(nx - tx) + abs(ny - ty)
                dist_o = abs(nx - ox) + abs(ny - oy)
                # If we can step onto a resource, strongly prefer it.
                on_res = 1 if (nx, ny) in res_set else 0
                score = (100000 * on_res) - (10 * dist_t) + (2 * dist_o) - (1 if (dx == 0 and dy == 0) else 0)
                if score > best_score:
                    best_score = score
                    best = [dx, dy]
        return best

    res_set = set(tuple(p) for p in resources)
    if resources:
        # Deterministically choose nearest resource by Manhattan distance, tie by lexicographic.
        tx, ty = min(resources, key=lambda p: (abs(p[0] - x) + abs(p[1] - y), p[0], p[1]))
        return best_move((tx, ty))
    else:
        # No resources: go to center while avoiding opponent a bit.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        move = best_move((cx, cy))
        return move