def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cd(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = w // 2, h // 2

    best_dx, best_dy = 0, 0
    best_val = -10**18

    # Heuristic shift: prioritize resources we can reach no later than opponent, else increase separation while drifting to center.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        sep_now = cd(nx, ny, ox, oy)
        center = -0.03 * cd(nx, ny, cx, cy)

        if resources:
            # Evaluate best claim potential among resources
            claim = -10**12
            for rx, ry in resources:
                ds = cd(nx, ny, rx, ry)
                do = cd(ox, oy, rx, ry)
                # Claim bonus: prefer resources where our next position is competitive (ds<=do)
                # Also reduce value if we are far behind.
                if ds <= do:
                    val = 3.0 / (1 + ds) + 1.0 * (do - ds) / (1 + do)
                else:
                    val = -2.2 * (ds - do) / (1 + ds) - 0.8 / (1 + ds)
                # Small tie-break toward nearer-to-opponent resources (denies them)
                val += 0.15 / (1 + do)
                if val > claim:
                    claim = val
            # Combine: if we can claim, focus; otherwise separation matters more.
            val_total = claim + 0.25 * sep_now + center
        else:
            val_total = 0.7 * sep_now + center

        # Deterministic tie-break: prefer moves with smaller dx^2+dy^2 (stability), then lexical order
        if val_total > best_val:
            best_val = val_total
            best_dx, best_dy = dx, dy
        elif val_total == best_val:
            if dx * dx + dy * dy < best_dx * best_dx + best_dy * best_dy:
                best_dx, best_dy = dx, dy
            elif dx * dx + dy * dy == best_dx * best_dx + best_dy * best_dy:
                if (dx, dy) < (best_dx, best_dy):
                    best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]