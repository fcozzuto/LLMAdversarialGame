def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    x, y, ox, oy = int(x), int(y), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(px, py):
        return 0 <= px < w and 0 <= py < h and (px, py) not in obstacles

    def d2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    best_move = (0, 0)
    best_score = -10**18

    opp_d = d2(x, y, ox, oy)
    use_competition = True

    for dxm, dym in moves:
        nx, ny = x + dxm, y + dym
        if not inside(nx, ny):
            continue

        if resources:
            best_adv = -10**18
            best_res_d = 10**18
            for rx, ry in resources:
                ds = d2(nx, ny, rx, ry)
                do = d2(ox, oy, rx, ry)
                # Advantage: prefer resources closer to us than opponent, but still generally progress.
                adv = (do - ds)
                if adv > best_adv:
                    best_adv = adv
                if ds < best_res_d:
                    best_res_d = ds

            # If we can directly steal (positive advantage), emphasize it; otherwise rush closest.
            if best_adv > 0 and use_competition:
                score = 1000 * best_adv - 0.01 * best_res_d
            else:
                score = -best_res_d + 0.25 * best_adv

            # Mild anti-zigzag: slightly prefer moves that do not increase distance to opponent too much.
            score += 0.0005 * (opp_d - d2(nx, ny, ox, oy))
        else:
            # No visible resources: move to reduce distance to opponent-side corner (likely where resources were).
            target_x = w - 1 if ox < w - 1 else w // 2
            target_y = h - 1 if oy < h - 1 else h // 2
            score = -d2(nx, ny, target_x, target_y) - 0.001 * d2(nx, ny, ox, oy)

        if score > best_score:
            best_score = score
            best_move = (dxm, dym)

    dxm, dym = best_move
    if not (-1 <= dxm <= 1 and -1 <= dym <= 1 and isinstance(dxm, int) and isinstance(dym, int)):
        return [0, 0]
    return [dxm, dym]