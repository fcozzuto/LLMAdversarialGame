def choose_move(observation):
    # Defensive default: stay in place
    dx = 0
    dy = 0

    # Helper to safely get fields
    def g(key, default=None):
        if isinstance(observation, dict):
            return observation.get(key, default)
        return default

    # Try to infer simple patterns from common fields
    # Default policy: try to move toward a locally closest resource or opponent if present.
    # Resource collection: look for "resources" or "resource" or "items" with coordinates
    # Pursuit-evasion: look for "evaders" or "enemies" with coordinates
    # Territory control: look for "threats" or "opponent" positions and "own" region

    # Gather potential targets
    targets = []

    for key in ("resources", "resource", "items", "targets"):
        if isinstance(g(key), list):
            for t in g(key):
                if isinstance(t, dict) and "pos" in t:
                    targets.append(tuple(t["pos"]))
        # also support single position
        if isinstance(g(key), dict) and "pos" in g(key):
            pos = tuple(g(key)["pos"])
            targets.append(pos)

    for key in ("evaders", "enemies", "opponents", "threats"):
        if isinstance(g(key), list):
            for t in g(key):
                if isinstance(t, dict) and "pos" in t:
                    targets.append(tuple(t["pos"]))
        if isinstance(g(key), dict) and "pos" in g(key):
            targets.append(tuple(g(key)["pos"]))

    # If we found targets, move towards the closest one within one step
    if targets:
        cx = g("you", g("position", (0, 0)))[0] if isinstance(g("you"), tuple) else 0
        cy = g("you", g("position", (0, 0)))[1] if isinstance(g("you"), tuple) else 0
        # If we can't determine own position, assume 0,0
        if not isinstance(g("position"), tuple):
            cx, cy = 0, 0
        # Compute closest target
        best = None
        bestd = None
        for tx, ty in targets:
            d = abs(tx - cx) + abs(ty - cy)
            if bestd is None or d < bestd:
                bestd = d
                best = (tx, ty)
        if best is not None and bestd is not None:
            tx, ty = best
            dx = 0 if tx == cx else (1 if tx > cx else -1)
            dy = 0 if ty == cy else (1 if ty > cy else -1)
            # Clamp to -1,0,1 just in case
            dx = -1 if dx < -1 else (1 if dx > 1 else dx)
            dy = -1 if dy < -1 else (1 if dy > 1 else dy)
            return [dx, dy]

    # Fallback: explore simple pattern depending on observation size
    # If we can see a neighbor obstacle or boundary, try to move diagonally away
    # Minimal heuristic: prefer right when nothing else
    # Respect boundaries if visible via "width" and "height" or "grid"
    w = g("width", g("grid_width", 0))
    h = g("height", g("grid_height", 0))
    if w and h:
        # keep within bounds with small bias
        dx = 0
        dy = 0
        # try to move right if possible
        dx = 1
        if w:
            dx = max(-1, min(1, 1))
        return [dx, dy]

    # Final safe default
    return [0, 0]
