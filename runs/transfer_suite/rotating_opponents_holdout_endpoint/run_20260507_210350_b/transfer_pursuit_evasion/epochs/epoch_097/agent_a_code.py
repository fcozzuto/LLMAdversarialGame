def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = observation.get("self_role") or "pursuer"
    if role not in ("pursuer", "evader"):
        role = "pursuer"

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def mobility_from(x, y, depth=3):
        if not inb(x, y):
            return -9999
        q = [(x, y, 0)]
        seen = {(x, y)}
        c = 0
        i = 0
        while i < len(q):
            cx, cy, d = q[i]
            i += 1
            c += 1
            if d >= depth:
                continue
            for dx, dy in moves:
                nx, ny = cx + dx, cy + dy
                if (nx, ny) not in seen and inb(nx, ny):
                    seen.add((nx, ny))
                    q.append((nx, ny, d + 1))
        return c

    best = None
    best_m = [0, 0]
    opp_mob = mobility_from(ox, oy, 3)

    # deterministic tie-break: fixed move order + stable scoring
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d2 = dist2(nx, ny, ox, oy)
        self_mob = mobility_from(nx, ny, 3)
        # pursuer: reduce distance, increase pressure by reducing opponent mobility (proxy)
        if role == "pursuer":
            # prefer moving toward opponent while also moving into/near tighter areas
            score = (-d2) * 100.0 + (-abs(self_mob - opp_mob)) * 0.2 + self_mob * 0.03 - (nx == ox and ny == oy) * 1e6
        else:
            # evader: maximize distance, avoid getting boxed (use local freedom)
            score = (d2) * 100.0 + self_mob * 1.0 - (abs(nx - (w - 1 - ox)) + abs(ny - (h - 1 - oy))) * 0.05

        if best is None or score > best:
            best = score
            best_m = [dx, dy]
    return [int(best_m[0]), int(best_m[1])]