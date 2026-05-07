def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def pt(p):
        if isinstance(p, dict):
            if "position" in p:
                p = p["position"]
            if "x" in p and "y" in p:
                return int(p["x"]), int(p["y"])
        return int(p[0]), int(p[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles") or []:
        x, y = pt(p)
        if inb(x, y):
            obst.add((x, y))

    resources = [pt(r) for r in (observation.get("resources") or [])]
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obst:
                return [dx, dy]
        return [0, 0]

    def manhattan(a, b, x, y):
        d1 = a - x
        if d1 < 0:
            d1 = -d1
        d2 = b - y
        if d2 < 0:
            d2 = -d2
        return d1 + d2

    cur_rem = int(observation.get("remaining_resource_count", len(resources)) or len(resources))
    best_move = (0, 0)
    best_val = None
    best_tie = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        # For each resource, estimate "advantage" if we are closer to it than opponent.
        # Prefer moves that (1) maximize advantage, (2) minimize our distance to the best target,
        # (3) maximize opponent denial when we are currently ahead/near.
        local_best_adv = None
        local_best_selfd = None
        for rx, ry in resources:
            selfd = manhattan(nx, ny, rx, ry)
            oppd = manhattan(ox, oy, rx, ry)
            adv = oppd - selfd  # positive means we are closer than opponent
            # Increase denial weight when resources are fewer (late game).
            wden = 1.0 + (12.0 / (cur_rem + 1.0))
            val = adv * wden - 0.01 * selfd
            if local_best_adv is None or val > local_best_adv or (val == local_best_adv and selfd < local_best_selfd):
                local_best_adv = val
                local_best_selfd = selfd

        # Also slightly penalize moves that increase our closest distance.
        # (deterministic and keeps policy stable)
        base_self = min(manhattan(sx, sy, rx, ry) for rx, ry in resources)

        # Final evaluation: prioritize best target advantage, then our best distance,
        # then smaller move magnitude to reduce oscillation.
        move_mag = abs(dx) + abs(dy)
        final_val = local_best_adv
        tie = (local_best_selfd, move_mag)

        if best_val is None or final_val > best_val or (final_val == best_val and tie < best_tie):
            best_val = final_val
            best_tie = tie
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]