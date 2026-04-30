def choose_move(observation):
    sx, sy = observation["self_position"]
    obstacles = observation.get("obstacles", [])
    resources = observation.get("resources", [])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obs_set = set((ox, oy) for ox, oy in obstacles)
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or ny < 0 or nx >= w or ny >= h:
                continue
            if (nx, ny) in obs_set:
                continue

            # Attraction to resources
            if resources:
                best_dist = 10**9
                nearest = None
                for rx, ry in resources:
                    d = abs(rx - nx) + abs(ry - ny)  # deterministic Manhattan
                    if d < best_dist:
                        best_dist = d
                        nearest = (rx, ry)
                rx, ry = nearest
                # Small tie-breakers to encourage progress and avoid zig-zag
                step_bias = (abs(rx - nx) < abs(rx - sx) or abs(ry - ny) < abs(ry - sy))
            else:
                best_dist = 0
                step_bias = False

            # Mild penalty for moving away from both coordinates
            away_pen = (1 if (abs(rx - nx) > abs(rx - sx)) else 0) + (1 if (abs(ry - ny) > abs(ry - sy)) else 0) if resources else 0

            # Encourage heading generally toward the nearest resource, including diagonals
            if resources:
                hx = 0 if rx == nx else (1 if rx > nx else -1)
                hy = 0 if ry == ny else (1 if ry > ny else -1)
                dir_score = 0
                if dx == hx:
                    dir_score += 1
                if dy == hy:
                    dir_score += 1
                if dx == hx and dy == hy:
                    dir_score += 1
            else:
                dir_score = 0

            # Avoid clustering too much with obstacles nearby (local safety)
            adj_obs = 0
            for adx in (-1, 0, 1):
                for ady in (-1, 0, 1):
                    tx, ty = nx + adx, ny + ady
                    if 0 <= tx < w and 0 <= ty < h and (tx, ty) in obs_set:
                        adj_obs += 1

            # Prefer staying only if it doesn't worsen resource distance
            stay_pen = 1 if (dx == 0 and dy == 0 and resources) else 0

            score = best_dist + 0.75 * adj_obs + 1.25 * away_pen - 0.35 * dir_score + stay_pen - (0.2 if step_bias else 0)
            candidates.append((score, dx, dy))

    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (t[0], t[1], t[2]))
    return [int(candidates[0][1]), int(candidates[0][2])]