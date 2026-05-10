def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("evade" in role) or ("escape" in role)
    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def free_options(x, y):
        c = 0
        for adx, ady in moves:
            nx, ny = x + adx, y + ady
            if inb(nx, ny) and (nx, ny) not in blocked:
                c += 1
        return c

    best = None
    bestv = -10**18
    # fixed tie-break by iteration order
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        d = dist2(nx, ny, ox, oy)
        local = free_options(nx, ny)
        cent = -(((nx - cx) ** 2) + ((ny - cy) ** 2))  # closer to center => larger cent

        if (nx, ny) == (ox, oy):
            v = (10**9) if not is_evader else -10**9
        else:
            if is_evader:
                # maximize survival: increase distance, prefer having options, slightly avoid center traps
                v = (d * 10.0) + (local * 2.0) + (cent * 0.2)
                # also slightly prefer moving away from closest obstacle
                min_ob = 10**18
                for px, py in blocked:
                    od = dist2(nx, ny, px, py)
                    if od < min_ob:
                        min_ob = od
                if min_ob < 10**18:
                    v += (min_ob * 0.05)
            else:
                # pursuer: minimize distance, maintain options, prefer center
                v = (-d * 10.0) + (local * 1.5) + (cent * 0.2)
                # avoid getting adjacent to obstacles when possible
                min_ob = 10**18
                for px, py in blocked:
                    od = dist2(nx, ny, px, py)
                    if od < min_ob:
                        min_ob = od
                if min_ob < 10**18:
                    v -= (min_ob < 4) * 50.0

        if v > bestv:
            bestv = v
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]