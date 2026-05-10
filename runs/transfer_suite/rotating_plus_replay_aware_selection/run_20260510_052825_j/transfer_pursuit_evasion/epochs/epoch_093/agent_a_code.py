def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    evader = ("evader" in role) or ("escape" in role) or ("runner" in role)

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def free(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx*dx + dy*dy

    corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]
    near_corner = min(corners, key=lambda c: dist2(sx, sy, c[0], c[1]))
    far_corner = max(corners, key=lambda c: dist2(ox, oy, c[0], c[1]))

    best_move = (0, 0)
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        # Bonus for moving roughly toward/away along the sign to opponent
        signx = 0 if ox == sx else (1 if ox > sx else -1)
        signy = 0 if oy == sy else (1 if oy > sy else -1)
        line_bonus = 0
        if evader:
            if dx == -signx or (dx == 0 and signx == 0):
                line_bonus += 1
            if dy == -signy or (dy == 0 and signy == 0):
                line_bonus += 1
            # Prefer running to the corner farthest from pursuer
            corner_bonus = dist2(nx, ny, far_corner[0], far_corner[1])
            val = d + 0.2 * corner_bonus + 0.05 * line_bonus
        else:
            if dx == signx or (dx == 0 and signx == 0):
                line_bonus += 1
            if dy == signy or (dy == 0 and signy == 0):
                line_bonus += 1
            corner_bonus = dist2(nx, ny, near_corner[0], near_corner[1])
            val = -d + 0.01 * (w*h - corner_bonus) + 0.05 * line_bonus  # avoid unnecessary corner wandering

        if best_val is None:
            best_val = val
            best_move = (dx, dy)
        else:
            if evader:
                if val > best_val:
                    best_val = val
                    best_move = (dx, dy)
            else:
                if val > best_val:
                    best_val = val
                    best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]