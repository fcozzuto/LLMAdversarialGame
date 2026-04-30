def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [W - 1, H - 1]) or [W - 1, H - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy  # Chebyshev for king-like movement

    rem = int(observation.get("remaining_resource_count", 0) or 0)
    endgame = rem <= 4

    best = [0, 0]
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        best_adv = -10**9
        best_dme = 10**9
        for rx, ry in resources:
            dme = dist(nx, ny, rx, ry)
            dop = dist(ox, oy, rx, ry)
            adv = dop - dme
            if adv > best_adv or (adv == best_adv and dme < best_dme):
                best_adv = adv
                best_dme = dme

        if resources:
            opp_dist = dist(nx, ny, ox, oy)
            center_pref = -abs(nx - (W - 1) / 2.0) - abs(ny - (H - 1) / 2.0)
            # Maximize: advantage first, then be closer to that target, then in endgame minimize opponent-nearness.
            key = (best_adv * (4 if endgame else 2), -best_dme, center_pref, (-opp_dist if endgame else opp_dist))
        else:
            # No resources: head toward center while keeping away from opponent slightly early.
            center_x = (W - 1) // 2
            center_y = (H - 1) // 2
            d_center = dist(nx, ny, center_x, center_y)
            opp_dist = dist(nx, ny, ox, oy)
            key = (-d_center, -opp_dist if endgame else opp_dist)

        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]

    return best