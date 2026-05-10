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

    self_role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in self_role) or ("runner" in self_role) or ("escape" in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def nearest_obst_d(x, y):
        if not obstacles:
            return 99
        best = 10**9
        for ax, ay in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d < best:
                best = d
        return best if best != 10**9 else 99

    def boundary_margin(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    best = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        d = abs(nx - ox) + abs(ny - oy)
        obst_d = nearest_obst_d(nx, ny)
        safe = boundary_margin(nx, ny)

        # 1-step lookahead: keep us consistent with role under our own next step
        # (deterministic, local, and cheap)
        want = 1 if is_evader else -1
        look = 0
        for adx, ady in moves:
            tx, ty = nx + adx, ny + ady
            if free(tx, ty):
                td = abs(tx - ox) + abs(ty - oy)
                look = td
                break

        score = want * d + (obst_d if not is_evader else 0.3 * obst_d) + (0.15 * safe if not is_evader else 0.05 * safe)
        if is_evader:
            score += -0.02 * look
        else:
            score += 0.02 * look

        if best is None or score > best:
            best = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]