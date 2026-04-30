def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs.sort(key=lambda t: (abs(t[0]) + abs(t[1]), t[0], t[1]))

    if not resources:
        return [0, 0]

    best_move = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Evaluate this move by how much it improves first-access to any resource.
        # Prefer maximizing (opponent_distance - my_distance), then minimizing my_distance.
        best_adv = None
        best_my = None
        best_rx, best_ry = None, None
        for rx, ry in resources:
            myd = dist_cheb(nx, ny, rx, ry)
            od = dist_cheb(ox, oy, rx, ry)
            adv = od - myd
            if best_adv is None or adv > best_adv or (adv == best_adv and (best_my is None or myd < best_my)) or (adv == best_adv and myd == best_my and (rx, ry) < (best_rx, best_ry)):
                best_adv, best_my = adv, myd
                best_rx, best_ry = rx, ry

        # Convert to a sortable deterministic value; also reward reducing opponent's advantage.
        cur_best_d = min(dist_cheb(sx, sy, rx, ry) for rx, ry in resources)
        val = (best_adv, -best_my)
        # Small tie-break: aim toward the selected resource deterministically.
        toward_dx = 0 if best_rx == nx else (1 if best_rx > nx else -1) if best_rx != nx else 0
        toward_dy = 0 if best_ry == ny else (1 if best_ry > ny else -1) if best_ry != ny else 0
        tie = (toward_dx != dx or toward_dy != dy, abs(nx - best_rx) + abs(ny - best_ry), cur_best_d)
        if best_val is None or val > best_val or (val == best_val and tie < best_tie):
            best_val = val
            best_tie = tie
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]