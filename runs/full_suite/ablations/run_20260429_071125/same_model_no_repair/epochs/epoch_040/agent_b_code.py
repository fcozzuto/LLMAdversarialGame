def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    grid_w, grid_h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def in_bounds(x, y):
        return 0 <= x < grid_w and 0 <= y < grid_h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    nearest = min(resources, key=lambda r: dist((sx, sy), r))
    tx, ty = nearest

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            d_before = abs(tx - sx) + abs(ty - sy)
            d_after = abs(tx - nx) + abs(ty - ny)
            toward = d_before - d_after  # positive is good
            opp_far = abs(nx - ox) + abs(ny - oy)
            # Small bias to reduce immediate movement away from target
            diag_bonus = 1 if (dx != 0 and dy != 0) else 0
            # Also lightly prefer not getting stuck by penalizing proximity to obstacles
            obst_near = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    if (nx + ax, ny + ay) in obstacles:
                        obst_near += 1
            score = 1000 * toward + 0.01 * opp_far + 0.1 * diag_bonus - obst_near
            moves.append((score, dx, dy))
    if not moves:
        return [0, 0]
    moves.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [int(moves[0][1]), int(moves[0][2])]