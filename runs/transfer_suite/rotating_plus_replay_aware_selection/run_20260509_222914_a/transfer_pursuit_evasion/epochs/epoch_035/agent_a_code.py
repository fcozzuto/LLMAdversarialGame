def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    self_role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in self_role) or ("runner" in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    obst_list = list(obstacles)

    def obstacle_penalty(x, y):
        if not obst_list:
            return 0.0
        # Strongly avoid stepping next to obstacles to reduce being corner-stuck
        best = 10**9
        for ax, ay in obst_list:
            d = abs(x - ax) + abs(y - ay)
            if d < best:
                best = d
        if best <= 1:
            return 50.0
        return 3.0 / best

    best_val = -10**18
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        dist = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        dman = abs(nx - ox) + abs(ny - oy)

        pen = obstacle_penalty(nx, ny)

        if is_evader:
            # Prefer maximizing distance; also prefer moving to safer corners/edges deterministically
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            corner_bonus = 0
            for cx, cy in corners:
                corner_bonus = max(corner_bonus, (abs(nx - cx) + abs(ny - cy)))
            # Encourage hugging edges a bit to limit pursuer lanes, but not if it means obstacle-adjacency
            edge_bonus = (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1)
            val = (dist * 2.5 + corner_bonus * 1.0 + (1.2 if edge_bonus else 0.0) + dman * 0.2) - pen
        else:
            # Prefer minimizing distance; slight tie-break toward edges to reduce escape options
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            edge_bonus = 0.0
            if nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1:
                edge_bonus = 0.15
            corner_push = 0.0
            for cx, cy in corners:
                corner_push = max(corner_push, -(abs(nx - cx) + abs(ny - cy)))
            # If capture radius were >0, we'd use it, but capture_radius is 0; still, quadratic distance works.
            val = (-dist * 3.0 - dman * 0.6 + edge_bonus * 1000.0 + corner_push * 0.1) - pen

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]