def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("evade" in role) or ("escape" in role) or ("evader" in str(observation.get("environment_name", "")).lower())

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    dist2 = lambda x1, y1, x2, y2: (x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def free_neighbors(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in blocked:
                c += 1
        return c

    best_move = [0, 0]
    best_score = -10**18

    # Small deterministic tie-break based on move order
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        d_cur = dist2(sx, sy, ox, oy)
        d_new = dist2(nx, ny, ox, oy)
        mob = free_neighbors(nx, ny)
        corner = max(corners, key=lambda c: -dist2(nx, ny, c[0], c[1]))
        corner_bonus = -dist2(nx, ny, corner[0], corner[1])

        # Additional penalty for "stepping onto" near-obstacle tightness
        near_obs = 0
        for bx, by in blocked:
            if dist2(nx, ny, bx, by) <= 4:
                near_obs += 1

        if is_evader:
            score = (d_new - d_cur) * 200 + d_new * 5 + mob * 2 + corner_bonus * 0.05 - near_obs * 1.5
            # Prefer not to move into direct pursuit line: reduce likelihood of closing distance too much
            score += (1 if d_new >= d_cur else -1) * (10 if d_new >= d_cur else 20)
        else:
            # Pursuer: minimize distance, increase mobility
            score = (d_cur - d_new) * 200 - d_new * 0.5 + mob * 2 - near_obs * 1.2
            # Encourage "forcing" by moving closer to the nearest corner away from evader (keeps them boxed)
            corner_opp = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
            score += -dist2(nx, ny, corner_opp[0], corner_opp[1]) * 0.03

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]