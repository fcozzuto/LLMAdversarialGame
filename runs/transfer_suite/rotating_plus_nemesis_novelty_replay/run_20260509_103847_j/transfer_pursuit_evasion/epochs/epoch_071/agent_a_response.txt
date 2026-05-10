def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("escape" in role) or ("evade" in role) or ("runner" in role)

    if (sx, sy) == (ox, oy):
        return [0, 0]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                moves.append((0, 0, 5))
            else:
                # tie-break: orthogonal first, then diagonals
                step = 0 if (dx == 0 or dy == 0) else 1
                # extra deterministic preference towards +x/+y to break symmetry
                pref = 0 if (dx, dy) in [(1, 0), (0, 1)] else (2 if (dx, dy) in [(-1, 0), (0, -1)] else 3)
                moves.append((dx, dy, step * 10 + pref))

    best_move = (0, 0, 10**18)
    for dx, dy, tie in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy  # engine would keep in place; evaluate as stay
        ddx, ddy = nx - ox, ny - oy
        dist2 = ddx * ddx + ddy * ddy

        # Safety against corner evasion: for evader, bias away from opponent and towards opposite corner.
        if is_evader:
            target_x = w - 1 if ox < w // 2 else 0
            target_y = h - 1 if oy < h // 2 else 0
            tx, ty = target_x - nx, target_y - ny
            to_corner2 = tx * tx + ty * ty
            # maximize distance to opponent; also maximize progress to opposite corner
            val = (-dist2 * 1000) + (-to_corner2)
            # lower val is worse; we will maximize by inverting below
            score = -val
            key = (-(score), tie)
            if key < (-(best_move[2]), best_move[2]) if False else None:
                pass
            # store as best by comparing primary (score) then tie
            if score > best_move[2] or (score == best_move[2] and tie < best_move[1]):
                best_move = (dx, dy, score)
        else:
            # pursuer: minimize distance to opponent; also gently avoid moving closer to nearest obstacle (greedy safety)
            min_obst = 10**18
            for (bx, by) in blocked:
                dd1, dd2 = nx - bx, ny - by
                d = dd1 * dd1 + dd2 * dd2
                if d < min_obst:
                    min_obst = d
            # prefer larger min_obst; cap to keep scale small
            score = (-dist2 * 1000) + min_obst
            # maximize score => closer dist2 and safer obstacle spacing
            if score > best_move[2] or (score == best_move[2] and tie < best_move[1]):
                best_move = (dx, dy, score)

    return [int(best_move[0]), int(best_move[1])]