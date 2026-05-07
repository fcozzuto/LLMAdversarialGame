def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Pick a resource we can beat next (or the best available if none)
    best_r = resources[0]
    best_key = (-10**9, 10**9)  # (opp-self, -self) maximized on first, minimized on second via negative

    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        adv = od - sd
        if sd == 0:
            key = (10**9, 0)
        else:
            key = (adv, -sd)
        # Prefer positive advantage; tie-break toward smaller self distance
        if key[0] > best_key[0] or (key[0] == best_key[0] and key[1] > best_key[1]):
            best_key = key
            best_r = [rx, ry]

    rx, ry = best_r

    # Move one step toward the chosen resource, but prefer moves that keep opponent farther from it
    best_move = [0, 0]
    best_score = (-10**18, 10**18, -10**18)  # (adv_to_target, -self_d, opp_d)

    for dx, dy in moves:
        nx, ny = int(sx + dx), int(sy + dy)
        if not valid(nx, ny):
            continue
        self_d = man(nx, ny, rx, ry)
        opp_d = man(ox, oy, rx, ry)
        adv = opp_d - self_d
        score = (adv, -self_d, opp_d)
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move