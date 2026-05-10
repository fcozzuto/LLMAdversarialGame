def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles") or []
    obs = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}
    role = observation.get("self_role", "pursuer")

    deltas = [(-1, -1), (1, 1), (-1, 1), (1, -1), (-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    prev_d = dist2(sx, sy, ox, oy)

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    def far_corner_from(px, py):
        return max(corners, key=lambda c: dist2(px, py, c[0], c[1]))
    def closest_corner_to(px, py):
        return min(corners, key=lambda c: dist2(px, py, c[0], c[1]))

    best_move = [0, 0]
    best_val = -10**18

    if role == "pursuer":
        # Greedy interception: maximize distance reduction; prefer diagonal progress and avoid dead-ends.
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            nd = dist2(nx, ny, ox, oy)
            improve = prev_d - nd  # primary
            v = improve * 10.0 - nd * 0.001
            # prefer moves that change both coordinates when it helps
            if dx != 0 and dy != 0:
                v += 0.02
            # small tie-break to keep moving generally toward opponent
            v += 0.001 * (abs(nx - ox) + abs(ny - oy)) * (-1)
            if v > best_val:
                best_val = v
                best_move = [dx, dy]
        return best_move

    # role == evader (or anything else): run to farthest corner, but reduce zigzag capture risk by "sticking" to a direction.
    tx, ty = far_corner_from(ox, oy)
    # Prefer staying away from the corner nearest pursuer to avoid being funneled.
    c2x, c2y = closest_corner_to(ox, oy)
    parity_now = (sx + sy) & 1

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd = dist2(nx, ny, ox, oy)
        # Primary: maximize distance; Secondary: drift toward escape corner; Tertiary: break zigzag by parity.
        v = nd * 1.0
        v += 0.03 * dist2(nx, ny, tx, ty)
        v -= 0.02 * dist2(nx, ny, c2x, c2y)
        v += 0.01 if ((nx + ny) & 1) != parity_now else -0.005
        if v > best_val:
            best_val = v
            best_move = [dx, dy]
    return best_move