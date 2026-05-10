def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position", [0, 0]) or [0, 0]
    o = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves.sort(key=lambda m: (m[0], m[1]))

    self_role = (observation.get("self_role") or "").lower()
    pursuer = ("purs" in self_role) or (self_role in ("captor", "pursuer"))
    evader = not pursuer

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist2(x, y, a, b):
        dx = x - a
        dy = y - b
        return dx * dx + dy * dy

    def mobility(x, y):
        cnt = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                cnt += 1
        return cnt

    best = None
    best_move = (0, 0)

    # Deterministic scoring:
    # pursuer: minimize distance, break ties by higher opponent mobility reduction
    # evader: maximize distance, break ties by higher mobility for self (avoid dead ends)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        if pursuer:
            if nx == ox and ny == oy:
                score = (-10**18, 0, 0)  # immediate capture
            else:
                d = dist2(nx, ny, ox, oy)
                opp_mob_after = mobility(ox, oy)
                self_mob = mobility(nx, ny)
                # Prefer smaller distance; slightly prefer reducing own freedom to keep commitment near center.
                score = (d, -opp_mob_after, -self_mob)
        else:
            d = dist2(nx, ny, ox, oy)
            self_mob = mobility(nx, ny)
            # Prefer escaping to open areas and away from immediate "trapping" by obstacles.
            corner_bias = min(nx, w - 1 - nx) + min(ny, h - 1 - ny)
            score = (-d, self_mob, corner_bias)

        if best is None or score < best:
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]