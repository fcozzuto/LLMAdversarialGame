def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def line_bias(cell, target):
        # encourage moving in the general direction of the best target
        cx, cy = cell
        tx, ty = target
        dx = 0 if tx == cx else (1 if tx > cx else -1)
        dy = 0 if ty == cy else (1 if ty > cy else -1)
        return dx, dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_key = None

    for dxm, dym in deltas:
        nx, ny = sx + dxm, sy + dym
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Choose the resource that maximizes *relative* progress vs opponent
        # (including tie-break on absolute closeness).
        best_cell_key = None
        for tx, ty in resources:
            sd = dist_cheb(nx, ny, tx, ty)
            od = dist_cheb(ox, oy, tx, ty)

            # If opponent is already very close, prefer routes that increase our lead or
            # reduce their access.
            # Priority components:
            # 1) maximize lead: od - sd
            # 2) minimize our distance
            # 3) favor reducing opponent distance (proxy by od after we move closer along direction)
            lead = od - sd
            absd = sd
            opp_after_proxy = od - (1 if (abs(dym) + abs(dxm)) > 0 else 0)

            # deterministic line alignment with target (slight)
            align_dx, align_dy = line_bias((nx, ny), (tx, ty))
            align = 1 if (align_dx == dxm and align_dy == dym) else 0

            key = (lead, -absd, opp_after_proxy, align)
            if best_cell_key is None or key > best_cell_key:
                best_cell_key = key

        if best_cell_key is None:
            continue

        # Final deterministic tie-break prefers staying/less movement if keys match
        move_mag = abs(dxm) + abs(dym)
        final_key = (best_cell_key, -move_mag, dxm, dym)
        if best_key is None or final_key > best_key:
            best_key = final_key
            best = (dxm, dym)

    return [int(best[0]), int(best[1])]