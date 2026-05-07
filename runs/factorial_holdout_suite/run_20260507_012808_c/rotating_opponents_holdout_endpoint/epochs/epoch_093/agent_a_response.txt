def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    denier = observation.get("opponent_role", "") == "resource_denier"
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_dx, best_dy = 0, 0
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        risk = 0
        for ax, ay in moves:
            px, py = nx + ax, ny + ay
            if (px, py) in obstacles:
                risk += 0.15

        target_val = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # If we're not closer, discourage unless we can still arrive sooner by next move structure.
            # Tie-break: prefer resources with larger (do-ds) and that we can reach quickly.
            lead = do - ds
            if denier:
                lead *= 1.15
            # Mild preference to avoid being "stolen" when equal distances.
            if lead == 0:
                lead -= 0.25
            # Obstacle proxy: if resource is near obstacles, slightly reduce (harder paths).
            obs_near = 0
            for ax, ay in moves:
                if (rx + ax, ry + ay) in obstacles:
                    obs_near += 1
            value = lead * 10.0 - ds * 0.35 - obs_near * 0.25
            if value > target_val:
                target_val = value
        total = target_val - risk
        # Deterministic tie-break: lowest resulting (nx,ny) lexicographically
        if total > best_score or (total == best_score and (nx, ny) < (sx + best_dx, sy + best_dy)):
            best_score = total
            best_dx, best_dy = nx - sx, ny - sy

    return [int(best_dx), int(best_dy)]