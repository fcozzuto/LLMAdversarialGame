def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev

    if not resources:
        for dx, dy in [(0,0),(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)]:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    moves = [(0,0),(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue

        my_step_pos = (nx, ny)
        # Choose the best target deterministically under a denier-aware score
        chosen = None
        chosen_val = None
        for rx, ry in resources:
            r = (rx, ry)
            md = dist(my_step_pos, r)
            od = dist((ox, oy), r)
            # Prefer closer resources; if opponent is closer, penalize heavily
            val = (-md) + (od * 0.25) - (15.0 if od <= md else 0.0)
            if chosen is None or val > chosen_val or (val == chosen_val and r < chosen):
                chosen, chosen_val = r, val

        if chosen is None:
            continue
        # Final move tie-break: prefer minimal distance to chosen target, then lexicographic move
        final_val = (chosen_val, -dist(my_step_pos, chosen), -((nx*10+ny)))
        if best_val is None or final_val > best_val or (final_val == best_val and (dx, dy) < best_move):
            best_val = final_val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]