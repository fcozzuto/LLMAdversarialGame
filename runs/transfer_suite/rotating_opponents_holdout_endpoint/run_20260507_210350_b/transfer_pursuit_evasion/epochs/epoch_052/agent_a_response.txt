def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    rolestr = (observation.get("self_role", "") or "").lower()
    is_evader = any(k in rolestr for k in ("evader", "escape", "flee", "runner"))
    turn = int(observation.get("turn_index", 0) or 0)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0: dx = -dx
        dy = y2 - y1
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obs_penalty(x, y):
        if not obstacles: return 0
        bestd = 999
        for ax, ay in obstacles:
            d = cheb(x, y, ax, ay)
            if d < bestd: bestd = d
            if bestd <= 0: break
        if bestd <= 0: return 1000
        # discourage hugging obstacles; slight preference for safe spacing
        return (3 - bestd) * 10 if bestd < 3 else 0

    # Deterministic tie-break order shift with turn parity to avoid repeating exact paths
    shift = turn % 9
    ordered = moves[shift:] + moves[:shift]

    best_move = (0, 0)
    best_score = -10**18 if is_evader else 10**18

    for dx, dy in ordered:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_opp = cheb(nx, ny, ox, oy)
        p = obs_penalty(nx, ny)

        # Additional deterministic bias: evader prefers moving away along axis when possible,
        # pursuer prefers closing on whichever coordinate differs more.
        if is_evader:
            # maximize distance, avoid obstacles
            score = d_opp * 100 - p
            if (nx - ox == 0) and (ny - oy == 0):
                score -= 100000  # avoid capture if possible
            # bias away direction
            score += (1 if (nx > ox) else -1 if (nx < ox) else 0) * (1 if dx != 0 else 0)
            score += (1 if (ny > oy) else -1 if (ny < oy) else 0) * (1 if dy != 0 else 0)
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
        else:
            # minimize distance, avoid obstacles
            score = d_opp * 100 + p
            # bias toward reducing larger coordinate gap
            score -= (1 if abs(ox - nx) < abs(ox - sx) else 0) * 3
            score -= (1 if abs(oy - ny) < abs(oy - sy) else 0) * 3
            if score < best_score:
                best_score = score
                best_move = (dx, dy)

    # If all moves invalid, stay
    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [dx, dy]