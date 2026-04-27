def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def adj_block(x, y):
        cnt = 0
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) in obstacles:
                cnt += 1
        return cnt

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        opp_d = md((nx, ny), (ox, oy))
        block = adj_block(nx, ny)

        if resources:
            val = -opp_d * 0.15 - block * 0.12
            for rx, ry in resources:
                sr = md((nx, ny), (rx, ry))
                orr = md((ox, oy), (rx, ry))
                closer = 1 if sr <= orr else -1
                lead = (orr - sr)
                gain = (1 + lead) if closer > 0 else (lead)
                # Prefer being the unique/clearer closer agent, still move toward generally close resources
                val += (gain * 3.0) - sr * 0.45
            # Small preference for center-ish to break ties deterministically
            val -= (abs((nx - (w-1)/2)) + abs((ny - (h-1)/2))) * 0.01

            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        else:
            # No resources: move to maximize distance from opponent and avoid obstacles
            val = -opp_d + block * 0.01 + (nx - (w-1)/2) * 0.001 + (ny - (h-1)/2) * 0.001
            if val > best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]