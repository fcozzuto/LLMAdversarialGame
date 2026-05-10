def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role", "") or "").lower()
    opp_role = str(observation.get("opponent_role", "") or "").lower()
    is_evader = ("evad" in self_role) or (("agent" in self_role) and ("evad" in opp_role))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    best_move = (0, 0)
    if not is_evader:
        best_score = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d2 = dist2(nx, ny, ox, oy)
            # Prefer reducing distance; lightly avoid getting adjacent to obstacles.
            adj_pen = 0
            for ox2, oy2 in obs:
                if dist2(nx, ny, ox2, oy2) <= 1:
                    adj_pen += 1
            score = -(10 * d2 + adj_pen)
            # Tie-break deterministically toward opponent direction (smallest dx,dy in lex order).
            if score > best_score or (score == best_score and (dx, dy) < best_move):
                best_score = score
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]
    else:
        # Evader: maximize distance from pursuer; keep away from obstacles.
        best_score = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d2 = dist2(nx, ny, ox, oy)
            adj_pen = 0
            for ox2, oy2 in obs:
                if dist2(nx, ny, ox2, oy2) <= 1:
                    adj_pen += 1
            # Also prefer moves that head toward the farthest corner when distances tie.
            corner_bonus = max(nx * nx + ny * ny, (w - 1 - nx) * (w - 1 - nx) + ny * ny,
                                nx * nx + (h - 1 - ny) * (h - 1 - ny),
                                (w - 1 - nx) * (w - 1 - nx) + (h - 1 - ny) * (h - 1 - ny))
            score = (10 * d2 + corner_bonus - 5 * adj_pen)
            if score > best_score or (score == best_score and (dx, dy) < best_move):
                best_score = score
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]