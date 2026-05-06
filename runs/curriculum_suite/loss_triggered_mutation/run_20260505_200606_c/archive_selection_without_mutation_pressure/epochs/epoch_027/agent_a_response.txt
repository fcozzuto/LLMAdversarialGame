def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    # Priority: (1) secure resources we can beat opponent for sooner, (2) deny by heading toward
    # resources the opponent is closest to, (3) avoid obstacles/bounds.
    best = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        val = 0
        for rx, ry in resources:
            d_our = md(nx, ny, rx, ry)
            d_opp = md(ox, oy, rx, ry)

            # If we can arrive strictly earlier, strongly favor.
            if d_our < d_opp:
                margin = d_opp - d_our
                val += 120 + 20 * margin
                # Extra weight for moving onto the resource row/col vicinity.
                val += 6 * (2 - abs(ny - ry) if abs(ny - ry) <= 2 else 0)
            else:
                # Deny: if opponent is closer, move to reduce our future contest.
                # Also give a smaller bias for being close even when behind.
                gap = d_our - d_opp
                val -= 15 + 3 * gap
                val += 2 * max(0, 4 - d_our)

        # Mild tie-break: progress upward (toward opponent corner likely) and toward center lines.
        val += 0.5 * (ny - sy) - 0.05 * (abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2))

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]