def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def pick_target():
        best = None
        best_key = None
        for (rx, ry) in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach sooner, then closer to us, then deterministic tie-break
            key = (do - ds, ds, ry * w + rx)
            if best is None or key > best_key:
                best = (rx, ry)
                best_key = key
        return best

    tx, ty = pick_target()

    best_move = [0, 0]
    best_score = None

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue

            # Smaller distance to target is better; being ahead vs opponent is best.
            ds_next = cheb(nx, ny, tx, ty)
            do_next = cheb(ox, oy, tx, ty)
            # Also add slight preference to reduce overall resource distance if target is poor
            self_to_target = ds_next
            opp_adv = (do_next - ds_next)

            # Minor deterministic tie-break favors moving "up-left" in scan order
            tie = (dx + 1) * 10 + (dy + 1)

            score = (opp_adv, -self_to_target, -cheb(nx, ny, ox, oy), -tie)
            if best_score is None or score > best_score:
                best_score = score
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]