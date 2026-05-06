def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position") or (0, 0))
    ox, oy = map(int, observation.get("opponent_position") or (w - 1, h - 1))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def best_step_from(pos):
        x, y = pos
        if not resources:
            return pos
        # Deterministic: chase the resource with smallest (dist, x, y)
        t = min(resources, key=lambda r: (dist(pos, r), r[0], r[1]))
        best = pos
        bestd = 10**9
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            nd = dist((nx, ny), t)
            if nd < bestd or (nd == bestd and (nx, ny) < best):
                bestd = nd
                best = (nx, ny)
        return best

    def eval_after(self_pos, opp_pos):
        if not resources:
            return 0, 0
        best_adv = -10**9
        best_selfd = 10**9
        for r in resources:
            sd = dist(self_pos, r)
            od = dist(opp_pos, r)
            adv = od - sd
            if adv > best_adv or (adv == best_adv and sd < best_selfd):
                best_adv = adv
                best_selfd = sd
        return best_adv, -best_selfd

    # Predict opponent one deterministic step using same logic
    opp_next = best_step_from((ox, oy))

    # Choose our step maximizing relative distance advantage to resources after prediction
    best_move = (0, 0)
    best_val = (-10**9, 10**9)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            val = eval_after((nx, ny), opp_next)
            if val > best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]