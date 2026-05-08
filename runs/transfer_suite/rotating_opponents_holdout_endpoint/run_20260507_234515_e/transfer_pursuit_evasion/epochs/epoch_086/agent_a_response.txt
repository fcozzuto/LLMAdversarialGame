def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    is_evader = "evader" in role

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def clamp_step(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_move = [0, 0]
    target_dir = (clamp_step(ox - sx), clamp_step(oy - sy))  # toward opponent

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in blocked:
            continue

        d = cheb(nx, ny, ox, oy)
        # obstacle pressure: prefer moves with fewer blocked neighbors around candidate
        nb = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                xx, yy = nx + ax, ny + ay
                if inside(xx, yy) and (xx, yy) in blocked:
                    nb += 1

        # Primary objective: chase or evade (evader maximizes distance, pursuer minimizes)
        primary = d if is_evader else -d
        # Secondary: reduce local blockage, tie-break toward/away from opponent direction
        dir_match = (dx == target_dir[0] and dy == target_dir[1]) or (dx == target_dir[0] and dy == 0 and target_dir[1] == 0) or (dx == 0 and dy == target_dir[1] and target_dir[0] == 0)
        dir_score = 1 if dir_match else 0
        if not is_evader:
            dir_score = dir_score  # encourage moving toward opponent
        else:
            # for evader, prefer moving away (opposite of target_dir)
            dir_score = 1 if (dx == -target_dir[0] and dy == -target_dir[1]) else 0

        score = primary * 1000 + (-nb) * 10 + dir_score
        if best is None or score > best or (score == best and (nx, ny) < (best_move[0] + sx, best_move[1] + sy)):
            best = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]