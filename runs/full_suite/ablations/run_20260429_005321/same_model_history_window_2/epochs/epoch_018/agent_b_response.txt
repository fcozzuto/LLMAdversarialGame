def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in (observation.get("obstacles") or []):
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def adj_obst_pen(x, y):
        pen = 0
        for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obst:
                pen += 1
        return pen

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dxm, dym in dirs:
        nx, ny = sx + dxm, sy + dym
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        # Target by "race advantage": (opponent_distance - self_distance) to the best resource.
        if resources:
            best_adv = -10**9
            best_res_d = None
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                adv = do - ds
                # tie-break: prefer closer own distance if same advantage
                if adv > best_adv or (adv == best_adv and (best_res_d is None or ds < best_res_d)):
                    best_adv = adv
                    best_res_d = ds
        else:
            best_adv = 0

        # Defensive shaping: keep some distance from opponent; also avoid hugging obstacles.
        d_opp = cheb(nx, ny, ox, oy)
        val = 10 * best_adv + 0.5 * d_opp - 0.75 * adj_obst_pen(nx, ny)

        # If behind (best_adv negative), prefer increasing distance to opponent and reducing own distance to any resource.
        if resources and best_adv < 0:
            min_ds = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            val += -1.0 * min_ds + 2.0 * d_opp

        if val > best_val:
            best_val = val
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]